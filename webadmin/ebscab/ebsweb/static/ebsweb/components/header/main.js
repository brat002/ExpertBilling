$(document).ready(function(e) {
	var animateIconClass = 'm-animate-shake';
	var animateBadgeClass = 'm-animate-blink';
	var $icon = $('.c-top-navbar .c-nav__link-icon.c-animated');
	var $badge = $('.c-top-navbar .c-nav__link-badge.c-animated');
	if ($icon && $badge) {
		setInterval(function() {
			$icon.addClass(animateIconClass);
			$badge.addClass(animateBadgeClass);
		}, 3000);
		setInterval(function() {
			$icon.removeClass(animateIconClass);
			$badge.removeClass(animateBadgeClass);
		}, 6000);
	}
});
