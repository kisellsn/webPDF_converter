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
    var dropArea = document.getElementById("dropArea");

    function resizeBlocks() {
        var dropAreaHeight = dropArea.offsetHeight;
        main.style.height = dropAreaHeight +130+ "px";
        centerDiv.style.height = dropAreaHeight +80+ "px";
    }

    window.onload = resizeBlocks;
    window.addEventListener("resize", resizeBlocks);

    var linkInput = document.getElementById('linkInput');
    var submitFilesButton = document.getElementById('submitFilesButton');
    var progressBar = document.getElementById('Progress_Status');




    linkInput.addEventListener('input', function() {
        if (linkInput.value.trim() !== '') {
            submitFilesButton.style.display = 'block';
        } else {
            submitFilesButton.style.display = 'none';
        }
    });

    submitFilesButton.addEventListener('click', function(e) {

        var link = linkInput.value;
        if (!link.startsWith('https://')) {
            link = 'https://' + link;
        }
        var url = '/web_convert';
        var data = { link: link };

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => {
            var statusCode = response.status;
            if (statusCode === 200) {
                window.location.href = '/result_pdf/convertedPage';
            } else {
                alert('Conversion error. The link may not exist.');
            }
        })
        .catch(error => {
            console.error('An error occurred when sending a request to the server:', error);
        });

        showProgressBar();

    });



});

