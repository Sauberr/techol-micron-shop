
function showMessage(message, type = 'success') {
    $('.container .alert').parent().remove();

    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const iconClass = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';

    const messageHtml = `
        <div class="container" style="padding-top: 90px;">
            <h6 id="message-timer" class="alert ${alertClass} text-center">
                <i class="fa ${iconClass}" aria-hidden="true"></i>
                &nbsp; ${message}
            </h6>
        </div>
    `;

    $('#header').after(messageHtml);

    hideMessageAfterTimeout();
}
