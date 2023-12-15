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


    var btnDownload = document.getElementById('load_button');

    btnDownload.addEventListener('click', function() {
        var download_logo = document.getElementById("btn-download");
        download_logo.classList.toggle('downloaded');

        var url = '/download';
        var newName = document.getElementById('name').value;

        var inputElement = document.getElementById('name');
        var fileName = inputElement.getAttribute('placeholder');
        var filetype = document.querySelector('#name_field p').innerText;


        var data = { newfilename: newName,  filename:fileName, filetype:filetype};
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        }).then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        }).then(blob => {
            var link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = newName ? newName + filetype : fileName + filetype;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

        })
        .catch(error => {
            console.error('An error occurred when sending a request to the server:', error);
        });
    });

    var downloadButtons = document.querySelectorAll('.btn-download');

    downloadButtons.forEach(function (button) {

        button.addEventListener('click', function () {
            var fileName = button.getAttribute('data-file-name').slice(0, -4);
            var filePath = button.getAttribute('data-file-path');
            var fileType = ".pdf";
            var newName = document.getElementById(fileName+".pdf").value;

            var url = '/download';
            var data = { newfilename: newName, filename: fileName, filetype: fileType };

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.blob();
                })
                .then(blob => {
                    var link = document.createElement('a');
                    link.href = URL.createObjectURL(blob);
                    link.download = newName ? newName + fileType : fileName + fileType;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                })
                .catch(error => {
                    console.error('An error occurred when sending a request to the server:', error);
                });
        });
    });






});

function toggleFilePreview(file_name) {
    var previewDiv = document.getElementById(file_name + 'Preview');
    if (previewDiv.style.display === 'none' || previewDiv.style.display === '') {
        previewDiv.style.display = 'block';
    } else {
        previewDiv.style.display = 'none';
    }
}
function hidePreview(file_name){
    var previewDiv = document.getElementById(file_name + 'Preview');
    previewDiv.style.display = 'none';
}