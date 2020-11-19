const adress = document.querySelector('#addressee');
const id_postbox = document.querySelector('#id-postbox');
const size = document.querySelector('#size');
valid_size = false;
validAdress = false;
valid_id_postbox = false;
const adressError = document.querySelector('#adressError');
const id_postboxError = document.querySelector('#id_postboxError');
const sizeError = document.querySelector('#sizeError');
const button = document.querySelector('#register');


adress.addEventListener('input', (evt )=>{
    const regExp = new RegExp("^[A-Za-z0-9 _]*[A-Za-z0-9][A-Za-z0-9 _]*$");
    if(!regExp.test(adress.value)){
        validAdress = false;
        adressError.innerText = "You can use only letters]";
        checkButton();
    }
    else{
        validAdress=true;
        adressError.innerText = "";
        checkButton();
    }
});

id_postbox.addEventListener('input', (evt )=>{
    const regExp = new RegExp("^[A-Za-z0-9 _]*[A-Za-z0-9][A-Za-z0-9 _]*$");
    if(!regExp.test(id_postbox.value)){
        valid_id_postbox = false;
        id_postboxError.innerText = "You can use only letters]";
        checkButton();
    }
    else{
        valid_id_postbox=true;
        id_postboxError.innerText = "";
        checkButton();
    }
});


size.addEventListener('input', (evt )=>{
    const regExp = new RegExp("^[A-Za-z0-9 _]*[A-Za-z0-9][A-Za-z0-9 _]*$");
    if(!regExp.test(size.value)){
        valid_size = false;
        sizeError.innerText = "You can use only letters]";
        checkButton();
    }
    else{
        valid_size=true;
        sizeError.innerText = "";
        checkButton();
    }
});

function checkButton() {
    if (valid_size && validAdress && valid_id_postbox) {
        button.disabled = false;
    } else {
        button.disabled = true;
    }
}

checkButton();