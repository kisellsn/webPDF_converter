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

    var uploadedFiles = [];

    function resizeBlocks() {
        var dropAreaHeight = dropArea.offsetHeight;
        main.style.height = dropAreaHeight +130+ "px";
        centerDiv.style.height = dropAreaHeight +80+ "px";
    }

    window.onload = resizeBlocks;
    window.addEventListener("resize", resizeBlocks);

    var fileInput = document.getElementById('fileInput');
    var submitFilesButton = document.getElementById('submitFilesButton');
    var progressBar = document.getElementById('Progress_Status');
    var previewArea = document.getElementById('previewArea');
    var uploadForm = document.getElementById('uploadForm');
    var selectedFiles = [];

    var uploadedText = document.querySelector(".uploaded");




    fileInput.addEventListener('change', function() {

        submitFilesButton.style.display = 'block';
        uploadForm.style.display = 'none';
        uploadedText.style.display = 'block';



        const files = Array.from(this.files);
        console.log(files);
        files.forEach((file) => {
            if (isValidFile(file)) {
                uploadedFiles.push(file);
                console.log(uploadedFiles)
                fileshow(file.name.split('.').slice(0, -1).join('.'), file.name.split('.').pop().toLowerCase());
            } else {
                alert('Invalid file format. Allowed extensions: .pdf');
            }
        });
    });

    submitFilesButton.addEventListener('click', function(e) {
        e.preventDefault();

        var uploadFormForm = document.querySelector('#uploadForm form');
        updateFileOrder();
        var fileInputFiles = fileInput.files;

        var formData = new FormData();
        var fileInputArray = Array.from(fileInputFiles);
        console.log(uploadedFiles)

        for (var i = 0; i < selectedFiles.length; i++) {
            var matchingFile = uploadedFiles.find(file => file.name === selectedFiles[i].fileName + '.' + selectedFiles[i].fileType);

            if (matchingFile) {
                formData.append('files[]', matchingFile);
            }
        }

        fetch('/split', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            var statusCode = response.status;
            if (statusCode === 200) {
                window.location.href = '/result_pdfs/resultZip';
            } else {
                alert('Conversion error. Something went wrong...');
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });

        showProgressBar();
    });


    dropArea.addEventListener('click', function() {
        fileInput.click();
    });
    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.add('dragover');
    });

    dropArea.addEventListener('dragleave', () => {
        dropArea.classList.remove('dragover');
    });

    dropArea.addEventListener('drop', function (e) {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.remove('dragover');


        submitFilesButton.style.display = 'block';
        uploadForm.style.display = 'none';
        uploadedText.style.display = 'block';

        const files = Array.from(e.dataTransfer.files);
        console.log(files);
        files.forEach((file) => {
             if (isValidFile(file)) {
                 uploadedFiles.push(file);
                 console.log(uploadedFiles)
                 fileshow(file.name.split('.').slice(0, -1).join('.'), file.name.split('.').pop().toLowerCase());
             } else {
                 alert('Invalid file format. Allowed extensions: .pdf');
             }
        });
    });

    function isValidFile(input) {
        var allowedExtensions = ['pdf'];

        var fileExtension = input.name.split('.').pop().toLowerCase();
        return allowedExtensions.includes(fileExtension);
    }


    function makeDraggable(draggable) {
        const container = document.getElementById('previewArea');
        draggable.addEventListener("dragstart", () =>{
            draggable.classList.add('dragging');
        });
        draggable.addEventListener("dragend", () =>{
            draggable.classList.remove('dragging');
        });

        container.addEventListener("dragover", e =>{
            e.preventDefault();
            e.stopPropagation();
            const afterElement = getDragAfterElement(container, e.clientY);
            const draggable = document.querySelector('.dragging');
            if(afterElement == null){
                 container.appendChild(draggable);
            }else{
                 container.insertBefore(draggable, afterElement);
            }

        });
    }
    function getDragAfterElement(container, y){
        const draggableElements =[...container.querySelectorAll('.showfilebox:not(.dragging)')];
        return draggableElements.reduce((closest, child)=>{
             const box = child.getBoundingClientRect();
             const offset =  y - (box.top + box.height / 2);
             if (offset <0 && offset>closest.offset){
                 return {offset: offset, element: child};
             }else{
                 return closest;
             }

        }, {offset: Number.NEGATIVE_INFINITY}).element
    }


    function fileshow(fileName, fileType){
        const showfileboxElem = document.createElement("div");
        showfileboxElem.classList.add("showfilebox");
        showfileboxElem.draggable = true;

        const leftElem = document.createElement("div");
        leftElem.classList.add("left");

        const fileTypeElem = document.createElement("span");
        fileTypeElem.classList.add("filetype");
        fileTypeElem.innerHTML = fileType;
        leftElem.append(fileTypeElem);

        const fileTitleElem = document.createElement("h3");
        fileTitleElem.innerHTML = fileName;
        leftElem.append(fileTitleElem);
        showfileboxElem.append(leftElem);

        const rightElem = document.createElement("div");
        rightElem.classList.add("right");
        showfileboxElem.append(rightElem);

        const crossElem = document.createElement("span");
        crossElem.innerHTML = "&#215;";
        rightElem.append(crossElem);


        makeDraggable(showfileboxElem);

        previewArea.append(showfileboxElem);


        selectedFiles.push({ fileName, fileType });

        crossElem.addEventListener("mousedown", (e) => {
            e.stopPropagation();


            const index = selectedFiles.findIndex((file) => file.fileName === fileName);
            if (index !== -1) {
                 selectedFiles.splice(index, 1);
            }
            console.log(selectedFiles);

            previewArea.removeChild(showfileboxElem);
            clearFileInput(fileInput.files);
            resizeBlocks();
        });


        resizeBlocks();
    }
    function updateFileOrder() {
        selectedFiles = Array.from(previewArea.querySelectorAll('.showfilebox')).map((box) => {
            const fileName = box.querySelector('h3').innerHTML;
            const fileType = box.querySelector('.filetype').innerHTML;
            return { fileName, fileType };
        });
    }
});

