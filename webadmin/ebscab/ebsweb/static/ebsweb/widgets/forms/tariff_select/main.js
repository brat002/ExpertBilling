!function() {
	var activeClass = 'border-primary';
	var $tariffSelectItems = $('.c-tariff-select__item');
	var $tariffSelectInputs = $('.c-tariff-select__item input');
	$tariffSelectInputs.on('change', function(e) {
		$tariffSelectItems.each(function(i) {
			var $this = $(this);
			if ($this.hasClass(activeClass)) {
				$this.removeClass(activeClass);
			}
		});
		$(this).parent().parent().parent().addClass(activeClass);
	});
}();
