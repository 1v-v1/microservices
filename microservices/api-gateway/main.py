from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import httpx
import json
import time
import redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import sys
import os
from typing import Optional, Dict, Any

# 添加共享模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.config.settings import settings
from shared.utils.auth import verify_token

app = FastAPI(
    title="API网关",
    description="统一入口、路由转发、负载均衡、认证授权、限流熔断",
    version="1.0.0"
)

# 限流器
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 信任主机中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Redis连接
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Prometheus指标
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'API request duration', ['method', 'endpoint'])
CIRCUIT_BREAKER_STATE = Counter('circuit_breaker_state_changes_total', 'Circuit breaker state changes', ['service', 'state'])

# 服务配置
SERVICES = {
    "user": {
        "url": settings.user_service_url,
        "timeout": 30,
        "circuit_breaker": {"failure_threshold": 5, "recovery_timeout": 60}
    },
    "loan": {
        "url": settings.loan_service_url,
        "timeout": 30,
        "circuit_breaker": {"failure_threshold": 5, "recovery_timeout": 60}
    },
    "repayment": {
        "url": settings.repayment_service_url,
        "timeout": 30,
        "circuit_breaker": {"failure_threshold": 5, "recovery_timeout": 60}
    },
    "risk": {
        "url": settings.risk_service_url,
        "timeout": 30,
        "circuit_breaker": {"failure_threshold": 5, "recovery_timeout": 60}
    },
    "notification": {
        "url": settings.notification_service_url,
        "timeout": 30,
        "circuit_breaker": {"failure_threshold": 5, "recovery_timeout": 60}
    },
    "file": {
        "url": settings.file_service_url,
        "timeout": 60,
        "circuit_breaker": {"failure_threshold": 5, "recovery_timeout": 60}
    }
}

# 路由配置
ROUTES = {
    "/api/users": "user",
    "/api/loans": "loan",
    "/api/repayments": "repayment",
    "/api/risk": "risk",
    "/api/notifications": "notification",
    "/api/files": "file",
    "/api/upload": "file",
    "/api/download": "file"
}

security = HTTPBearer(auto_error=False)


class CircuitBreaker:
    def __init__(self, service_name: str, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                CIRCUIT_BREAKER_STATE.labels(service=self.service_name, state="HALF_OPEN").inc()
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def on_success(self):
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.failure_count = 0
            CIRCUIT_BREAKER_STATE.labels(service=self.service_name, state="CLOSED").inc()
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            CIRCUIT_BREAKER_STATE.labels(service=self.service_name, state="OPEN").inc()


# 熔断器实例
circuit_breakers = {service: CircuitBreaker(service, **config["circuit_breaker"]) 
                   for service, config in SERVICES.items()}


def get_service_from_path(path: str) -> Optional[str]:
    """根据路径获取服务名"""
    for route, service in ROUTES.items():
        if path.startswith(route):
            return service
    return None


def get_service_url(service: str, path: str) -> str:
    """获取服务URL"""
    base_url = SERVICES[service]["url"]
    # 移除API前缀
    if path.startswith("/api/"):
        path = path[4:]  # 移除 "/api"
    return f"{base_url}{path}"


async def forward_request(service: str, method: str, url: str, headers: Dict[str, str], 
                         body: Optional[bytes] = None, params: Optional[Dict[str, Any]] = None) -> tuple:
    """转发请求"""
    timeout = SERVICES[service]["timeout"]
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body,
                params=params
            )
            return response.status_code, response.headers, response.content
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="服务超时"
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="服务不可用"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"请求转发失败: {str(e)}"
            )


def authenticate_request(credentials: Optional[HTTPAuthorizationCredentials] = None) -> Optional[Dict[str, Any]]:
    """认证请求"""
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        return payload
    except Exception:
        return None


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """指标中间件"""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    method = request.method
    endpoint = request.url.path
    
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response.status_code).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """限流中间件"""
    # 对特定路径进行限流
    if request.url.path.startswith("/api/"):
        client_ip = get_remote_address(request)
        key = f"rate_limit:{client_ip}"
        
        # 使用Redis实现滑动窗口限流
        current_time = int(time.time())
        window_size = 60  # 1分钟窗口
        max_requests = 100  # 最大请求数
        
        pipe = redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, current_time - window_size)
        pipe.zcard(key)
        pipe.zadd(key, {str(current_time): current_time})
        pipe.expire(key, window_size)
        
        results = pipe.execute()
        current_requests = results[1]
        
        if current_requests >= max_requests:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "请求过于频繁，请稍后再试"}
            )
    
    response = await call_next(request)
    return response


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_request(
    path: str,
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """代理请求到相应的微服务"""
    # 获取服务名
    service = get_service_from_path(f"/{path}")
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    # 检查熔断器状态
    circuit_breaker = circuit_breakers[service]
    if not circuit_breaker.can_execute():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="服务暂时不可用，请稍后再试"
        )
    
    # 认证（除了公开接口）
    auth_payload = None
    if not path.startswith(("health", "metrics")):
        auth_payload = authenticate_request(credentials)
        if not auth_payload and service != "user":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="需要认证"
            )
    
    # 构建目标URL
    target_url = get_service_url(service, f"/{path}")
    
    # 准备请求头
    headers = dict(request.headers)
    if auth_payload:
        headers["X-User-ID"] = str(auth_payload.get("user_id", ""))
        headers["X-Username"] = auth_payload.get("sub", "")
    
    # 移除不需要的头部
    headers.pop("host", None)
    headers.pop("content-length", None)
    
    # 读取请求体
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    # 获取查询参数
    params = dict(request.query_params)
    
    try:
        # 转发请求
        status_code, response_headers, response_content = await forward_request(
            service, request.method, target_url, headers, body, params
        )
        
        # 更新熔断器状态
        circuit_breaker.on_success()
        
        # 返回响应
        return JSONResponse(
            status_code=status_code,
            content=json.loads(response_content.decode()) if response_content else {},
            headers=dict(response_headers)
        )
    
    except HTTPException as e:
        # 更新熔断器状态
        circuit_breaker.on_failure()
        raise e


@app.get("/health")
async def health_check():
    """健康检查"""
    service_status = {}
    
    for service, config in SERVICES.items():
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{config['url']}/health")
                service_status[service] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception:
            service_status[service] = {
                "status": "unhealthy",
                "response_time": None
            }
    
    overall_status = "healthy" if all(
        status["status"] == "healthy" for status in service_status.values()
    ) else "degraded"
    
    return {
        "status": overall_status,
        "services": service_status,
        "timestamp": time.time()
    }


@app.get("/metrics")
async def metrics():
    """Prometheus指标"""
    from fastapi.responses import Response
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/circuit-breaker/status")
async def circuit_breaker_status():
    """熔断器状态"""
    status = {}
    for service, cb in circuit_breakers.items():
        status[service] = {
            "state": cb.state,
            "failure_count": cb.failure_count,
            "last_failure_time": cb.last_failure_time
        }
    return status


@app.post("/circuit-breaker/reset/{service}")
async def reset_circuit_breaker(service: str):
    """重置熔断器"""
    if service not in circuit_breakers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    circuit_breakers[service].state = "CLOSED"
    circuit_breakers[service].failure_count = 0
    circuit_breakers[service].last_failure_time = None
    
    return {"message": f"熔断器 {service} 已重置"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


