const url = 'uploadSVG';
const input = document.getElementById('fileUpload');

const upload = (file) => {
    fetch(url, { // Your POST endpoint
        method: 'POST',
        //   headers: {
        //     "Content-Type": ""
        //   },
        body: file // This is your file object
    }).then(
        success => console.log(success) // Handle the success response object
    ).catch(
        error => console.log(error) // Handle the error response object
    );
};

const onSelectFile = () => upload(input.files[0]);
input.addEventListener('change', onSelectFile, false);