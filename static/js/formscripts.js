function fileValidation(filename) {

    var fileInput =
        document.getElementById(filename);
     
    var filePath = (fileInput.value).toLowerCase();
 
    // Allowing file type
    var allowedExtensions =
            /(\.jpg|\.jpeg|\.png|\.gif)$/i;
     
    if (!allowedExtensions.exec(filePath)) {
        alert('Invalid file type. Please enter only image files.');
        fileInput.value = '';
        
    }
   
    }
   
function submitForm(frmName) {
        document.getElementById(frmName).submit();
    
}

function submitForm1(id,acceptID,emailID) {
    document.getElementById('coachID').value=id;
    document.getElementById('acceptID').value=acceptID;
    document.getElementById('emailID').value=emailID;
    document.getElementById('adminForm').submit();

}

function addRows(divName) {
    var myDiv = document.getElementById(divName);
    myDiv.style.display = "block"; 
}

function displayRow(divName,imgName) {
    var myDiv = document.getElementById(divName);
    myDiv.style.display = "block"; 
    var myImg = document.getElementById(imgName);
    myImg.style.display = "none"; 
    
}

// Function to update the result field
function updateResult(maxVal) {
    text1 = document.getElementById("amtRecieved1");
    text2 = document.getElementById("amtRecieved2");
    text3 = document.getElementById("amtRecieved3");
    text4 = document.getElementById("amtRecieved4");
    text5 = document.getElementById("amtRecieved5");

    varSum = parseFloat(text1.value) || 0 +  parseFloat(text2.value) || 0 + parseFloat(text3.value) || 0 +  parseFloat(text4.value) || 0 +  parseFloat(text5.value) || 0;
    
    amtPending = document.getElementById("amtPending");
    varRes = maxVal - varSum;
    amtPending.value = Math.abs(varRes);
}
