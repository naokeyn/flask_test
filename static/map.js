window.onload = function() {
    const loading = document.getElementById('loading');
    loading.classList.add('loaded');
}

let rewrite = (target) => {

    let source

    if (target == "start") {
        source = "end"
    } else {
        source = "start"
    }

    let sourceElement = document.getElementById(source)
    let targetElement = document.getElementById(target)
    let selected = sourceElement.value
    let len = targetElement.length

    for (let i = 0; i < len; i++) {
        if (targetElement[i].value == selected) {
            targetElement[i].setAttribute("disabled", true)
        }
        else {
            targetElement[i].removeAttribute("disabled")
        }
    }
}