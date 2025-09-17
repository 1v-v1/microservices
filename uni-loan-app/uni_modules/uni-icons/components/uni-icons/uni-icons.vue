<template>
	<view :class="['uni-icons', 'icon-' + type]" :style="{ color: color, 'font-size': size + 'px' }" @click="_onClick"></view>
</template>

<script>
	export default {
		name: 'UniIcons',
		props: {
			type: {
				type: String,
				default: ''
			},
			color: {
				type: String,
				default: '#333333'
			},
			size: {
				type: [Number, String],
				default: 16
			},
			customIcons: {
				type: String,
				default: ''
			}
		},
		methods: {
			_onClick() {
				this.$emit('click')
			}
		}
	}
</script>

<style lang="scss">
	.uni-icons {
		display: inline-block;
		font-style: normal;
		text-align: center;
		position: relative;
	}
	
	/* 替代图标实现 - 使用伪元素显示简单图形 */
	.icon-weixin::before {
		content: "W";
		font-weight: bold;
	}
	
	.icon-camera::before {
		content: "📷";
	}
	
	.icon-headphones::before {
		content: "🎧";
	}
	
	.icon-info::before {
		content: "i";
		font-style: italic;
		font-weight: bold;
	}
	
	.icon-locked::before {
		content: "🔒";
	}
	
	.icon-wallet::before {
		content: "💼";
	}
	
	.icon-paperplane::before {
		content: "✈";
	}
	
	.icon-shield-filled::before {
		content: "🛡";
	}
	
	.icon-personadd::before {
		content: "👤+";
	}
	
	.icon-auth::before {
		content: "✓";
		font-weight: bold;
	}
	
	.icon-medal::before {
		content: "🏅";
	}
	
	.icon-help::before {
		content: "?";
		font-weight: bold;
	}
	
	.icon-refresh::before, .icon-refreshempty::before {
		content: "↻";
	}
	
	.icon-phone::before {
		content: "📞";
	}
	
	.icon-compose::before {
		content: "✎";
	}
	
	.icon-warning::before {
		content: "⚠";
	}
	
	.icon-person::before {
		content: "👤";
	}
	
	.icon-eye::before {
		content: "👁";
	}
	
	.icon-arrowright::before {
		content: "→";
	}
	
	.icon-checkmarkempty::before {
		content: "✓";
	}
</style> 