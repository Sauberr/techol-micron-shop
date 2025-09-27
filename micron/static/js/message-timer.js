function hideMessageAfterTimeout() {
    var message_timeout = document.getElementById("message-timer");
    if (message_timeout) {
        setTimeout(function() {
            message_timeout.style.display = "none";
        }, 2500);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    hideMessageAfterTimeout();
});
