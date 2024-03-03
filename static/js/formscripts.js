function fileValidation(filename) {
    var fileInput =
        document.getElementById(filename);
         var filePath = (fileInput.value).toLowerCase();
 
    // Allowing file type
    var allowedExtensions =
            /(\.jpg|\.jpeg|\.png|\.gif)$/i;
    
    if (!allowedExtensions.test(filePath)) {
        alert('Invalid file type. Please enter only image files.');
        fileInput.value = '';
        
    }
   
}
   
function submitForm(frmName) {
        document.getElementById(frmName).submit();
    
}


function submitForm2(requestID) {
    var confirmDelete = confirm("Are you sure you want to delete this request?");
    alert(document.getElementById('type').value);
    if (confirmDelete) {
        document.getElementById('requestID').value=requestID;
        document.getElementById('requestDeleteForm').submit();
    }
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
    var text1 = parseFloat(document.getElementById("amtRecieved1").value) || 0;
    var text2 = parseFloat(document.getElementById("amtRecieved2").value) || 0;
    var text3 = parseFloat(document.getElementById("amtRecieved3").value) || 0;
    var text4 = parseFloat(document.getElementById("amtRecieved4").value) || 0;
    var text5 = parseFloat(document.getElementById("amtRecieved5").value) || 0;

    var varSum = text1 + text2 + text3 + text4 + text5; 
    amtPending = document.getElementById("amtPending");
    varRes = maxVal - varSum;
    amtPending.value = varRes;
   
}
