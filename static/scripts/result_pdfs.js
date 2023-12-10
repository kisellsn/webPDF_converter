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

    function addShowFileBox(file) {


        const showfilebox = document.createElement('div');
        showfilebox.className = 'showfilebox';

        const leftPart = document.createElement('div');
        leftPart.className = 'left';

        const fileTypeSpan = document.createElement('span');
        fileTypeSpan.className = 'filetype';
        fileTypeSpan.textContent = 'PDF';
        leftPart.appendChild(fileTypeSpan);

        const pdfInfo = document.createElement('div');
        pdfInfo.className = 'pdf_info';

        const inputFileName = document.createElement('input');
        inputFileName.type = 'text';
        inputFileName.className = 'form__field_pdf';
        inputFileName.placeholder = file.file_name;
        inputFileName.name = 'result';
        inputFileName.required = true;
        pdfInfo.appendChild(inputFileName);

        const sizeFieldPdf = document.createElement('div');
        sizeFieldPdf.className = 'size_field_pdf';

        sizeFieldPdf.innerHTML = `<p>${file.file_size} mb -</p><p>${file.pages_count} pages</p>`;
        pdfInfo.appendChild(sizeFieldPdf);

        leftPart.appendChild(pdfInfo);


        const rightPart = document.createElement('div');
        rightPart.className = 'right';


        const downloadButton = document.createElement('div');
        downloadButton.className = 'btn-download';
        downloadButton.innerHTML = `
          <svg width="22px" height="16px" viewBox="0 0 22 16">
            <!-- Ваш SVG-код тут -->
          </svg>
        `;

        downloadButton.addEventListener('click', () => downloadFile(file.file_name));
        rightPart.appendChild(downloadButton);

        showfilebox.appendChild(leftPart);
        showfilebox.appendChild(rightPart);

        leftDiv.appendChild(showfilebox);
      }


      function downloadFile(fileName) {
        // Ваш код для завантаження файлу
        console.log(`Downloading file: ${fileName}`);
        // Додайте реальний код для завантаження файлу
      }
      const leftDiv = document.getElementById('left_div');

      var filess = document.getElementById("left_div").dataset.files;
      console.log(filess);
      const files = JSON.parse(JSON.stringify(filess));
      console.log(files);
      for (const file of files) {
          console.log(file);
      }




});

