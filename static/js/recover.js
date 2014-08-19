$(document).on("click", "#recoverUsernameBtn", function () {
	$("#recoverUsername").removeClass("hidden");
	$("#recoverPassword").addClass("hidden");
});

$(document).on("click", "#recoverPasswordBtn", function () {
	$("#recoverUsername").addClass("hidden");
	$("#recoverPassword").removeClass("hidden");
});