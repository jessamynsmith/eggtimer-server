var addFormStyles = function() {
    $('select,input[type="text"],input[type="datetime"],input[type="date"],input[type="time"],input[type="number"]').addClass('form-control').addClass('my-form-control');
    $('label').addClass('control-label').addClass('my-control-label');
};


var setRequiredLabels = function(ids) {
    $('label').removeClass('required');
    $('input,textarea,select').filter('[required]:visible').parent().parent().find("label").addClass("required");
};


$(document).ready(function() {
    addFormStyles();
});
