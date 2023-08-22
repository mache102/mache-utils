// listen for a div with class= "end-level"
// when found, log all the text in that div
// then click the button in that class (there will be only one button)

setInterval(function () {
    var endLevel = document.getElementsByClassName("end-level");

    if (endLevel.length > 0) {
        console.log(endLevel[0].innerText);
        endLevel[0].getElementsByTagName("button")[0].click();
    }
});


// get the variable localStorage.getItem("ZombieData")
// and download as json file
// https://stackoverflow.com/questions/19721439/download-json-object-as-a-file-from-browser

function downloadObjectAsJson(exportObj, exportName){
    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportObj));
    var downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href",     dataStr);
    downloadAnchorNode.setAttribute("download", exportName + ".json");
    document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
}

function downloadZombieData() {
    zombieData = JSON.parse(localStorage.getItem("ZombieData"));
    downloadObjectAsJson(zombieData, "zombieData");
}

downloadZombieData();