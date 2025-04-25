// onclick="return openSocialPopup(this.href, '{{ backend_name }}')"
function openSocialPopup(url, provider) {
    const width = 600;
    const height = 700;
    const left = (screen.width / 2) - (width / 2);
    const top = (screen.height / 2) - (height / 2);
    const popup = window.open(
        url,
        `login_${provider}`,
        `width=${width},height=${height},top=${top},left=${left},resizable,scrollbars=yes`
    );

    if (popup) {
        popup.focus();
        return false; // Prevent default link behavior
    } else {
        alert("Please allow popups for this website");
        return true;
    }
}
