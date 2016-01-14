$(document).ready( function() {
	setTimeout("$('.status').fadeOut(1000)", 5000);
	$("#push_notification").click(function(event) {
		event.preventDefault();
		if (confirm("Are you sure you want to send this push notification?") == true) {
			$("input[name='_send_push'").val('1');
			$("form.update").submit();
		}
	});
});