/*
 * jQuery Hoverbox 1.0
 * http://koteako.com/hoverbox/
 *
 * Copyright (c) 2009 Eugeniy Kalinin
 * Dual licensed under the MIT and GPL licenses.
 * http://koteako.com/hoverbox/license/
 */
jQuery.fn.hoverbox=function(a){var b=jQuery.extend({id:"tooltip",top:0,left:15},a);var d;function c(e){if(!d){d=$('<div style="position:absolute" id="'+b.id+'"></div>').appendTo(document.body).hide()}if(e){d.css({top:(e.pageY-b.top)+"px",left:(e.pageX+b.left)+"px"})}return d}this.each(function(){$(this).hover(function(f){if(this.title){this.t=this.title;this.title="";this.alt="";c(f).html(this.t).fadeIn("fast")}},function(){if(this.t){this.title=this.t;c().hide()}});$(this).mousemove(c)})};