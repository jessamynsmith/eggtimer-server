addFormStyles = function() {
    $('select,input[type="text"],input[type="datetime"],input[type="date"],input[type="time"],input[type="number"]').addClass('form-control').addClass('my-form-control');
    $('label').addClass('control-label').addClass('my-control-label');
};

$(document).ready(function() {
    addFormStyles();
});
