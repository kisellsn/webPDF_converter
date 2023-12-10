function update() {
    var element = document.getElementById("myprogressBar");
    var width = 1;
    var identity = setInterval(scene, 10);
    function scene() {
        if (width >= 100) {
            clearInterval(identity);
        } else {
            width++;
            element.style.width = width + '%';
            var progressBarText = document.getElementById("progressBarText");
            progressBarText.innerHTML = "Opening " + width + "%";
        }
    }

}
function showProgressBar() {
    document.getElementById("Progress_Status").style.display = "block";
    update();
}
document.addEventListener('DOMContentLoaded', function() {
    var main = document.querySelector("main");
    var centerDiv = document.getElementById("center_div");



    var fileInput = document.getElementById('fileInput');
    var submitFilesButton = document.getElementById('submitFilesButton');
    var progressBar = document.getElementById('Progress_Status');
    var previewArea = document.getElementById('previewArea');
    var uploadForm = document.getElementById('uploadForm');
    var selectedFiles = [];

    var uploadedText = document.querySelector(".uploaded");




    var convertButton = document.getElementById('convert_f');
    var webConvertButton = document.getElementById('webconvert_f');
    var mergeButton = document.getElementById('merge_f');

    convertButton.addEventListener('click', function() {
        window.location.href = 'convert_to_pdf';
    });

    webConvertButton.addEventListener('click', function() {
        window.location.href = 'convert_web_to_pdf';
    });

    mergeButton.addEventListener('click', function() {
        window.location.href = 'merge_pdf';
    });
});

