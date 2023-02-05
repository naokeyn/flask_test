let rewrite = (target) => {

    const near_nodes = [
        ["野球場", "ラグビー場", "投てき場", "ゴルフ練習場"],
        ["経済学部研究棟", "経済学部B棟"],
        ["納品検収センター", "教職員駐車場", "防災備蓄品倉庫"]
    ]

    let source

    if (target == "start") {
        source = "end"
    }
    else {
        source = "start"
    }

    let sourceElement = document.getElementById(source)
    let targetElement = document.getElementById(target)
    let selected = sourceElement.value
    let len = targetElement.length

    // 選択された地点を非表示
    for (let i = 0; i < len; i++) {
        if (targetElement[i].value == selected) {
            targetElement[i].setAttribute("disabled", true)
        }
        else {
            targetElement[i].removeAttribute("disabled")
        }
    }

    for (let i = 0; i < near_nodes.length; i++) {
        if (near_nodes[i].includes(selected)) {

            for (let j = 0; j < near_nodes[i].length; j++) {
                for (let k = 0; k < len; k++) {

                    if(targetElement[k].value == near_nodes[i][j]){
                        targetElement[k].setAttribute("disabled", true)
                    }
                }
            }
        }
    }
}