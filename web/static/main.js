const loginInput = document.querySelector('#login-input');
const firstNameInput = document.querySelector('#firstname');
const lastNameInput = document.querySelector('#lastname');
const loginError = document.querySelector('#login-error');
const loginGood = document.querySelector('#login-good');
const button = document.querySelector('#register');
const email = document.querySelector('#email');

const BASE_URL = '/sender/isLogin';
const errorMessagelogin = 'Username has already exist';
const errorMessageLogin2 = 'Login has to have between 4 and 12 chars!';
let validName = false;
let validPassword = false;
let validLogin = false;
let validEmail = false;
const passwordInput1 = document.querySelector('#password-input1');
const passwordInput2 = document.querySelector('#password-input2');
const passwordError1 = document.querySelector('#password-error1');
const firstNameError = document.querySelector('#firstname-error');
const lastNameError = document.querySelector('#lastname-error');
const passwordError2 = document.querySelector('#password-error2');
const emailError = document.querySelector('#email-error');

const request = async (endpoint) => {
    return await fetch(`${BASE_URL}/${endpoint}`)
        .then(response => response.json())
}


const isInputTextMatch = (inputText, username) => {
    const regex = new RegExp(`^${inputText}`, "i");
    return regex.test(username)
}

firstNameInput.addEventListener('input', (evt )=>{
    const regExp = new RegExp("[A-ZŻŹĆĄŚĘŁÓŃ][a-zzżźćńółęąś]");
    if(!regExp.test(firstNameInput.value)){
        validName = false;
        firstNameError.innerText = "Name has to have  first letter big = [A-Z{PL}][a-z{pl}]";
        checkButton();
    }
    else{
        firstNameError.innerText = "";
        validName=true;
        checkButton();
    }
});

lastNameInput.addEventListener('input', (evt )=>{
    const regExp = new RegExp("[A-ZŻŹĆĄŚĘŁÓŃ][a-zzżźćńółęąś]");
    if(!regExp.test(lastNameInput.value)){
        validName = false;
        lastNameError.innerText = "last name has to have  first letter big = [A-Z{PL}][a-z{pl}]";
        checkButton();
    }
    else{
        validName=true;
        lastNameError.innerText = "";
        checkButton();
    }
});
//email

email.addEventListener('input', (evt )=>{

    if(!email.value.toString().includes("@")){
        emailError.innerText = "E-mail is incorrect";
        validEmail = false;

    }
    else{
        validEmail=true;
        emailError.innerText = "";
        checkButton();
    }
});



loginInput.addEventListener('input', (event) => {
      event.preventDefault();
      const inputText = event.target.value;
    if (inputText.trim().length < 4 || inputText.trim().length > 12) {
        loginGood.innerText = "";
        loginError.innerHTML = errorMessageLogin2;
        validLogin = false;
        checkButton();
    } else {
        loginError.innerHTML = ""
        request(loginInput.value).then(response => {
            if (response['user'] === "available") {
                validLogin = true;
                loginError.innerText = "";
                loginGood.innerText = "Login is available";
                checkButton();
            } else if (response['user'] === "taken") {
                loginGood.innerText = "";
                loginError.innerText = errorMessagelogin;
                validLogin = false;
                checkButton();
            }
            else{
                validLogin = false;
                loginGood.innerText = "";
                loginError.innerText = "";
            }
        })
    }
});
passwordInput1.addEventListener('input', (event) => {
    event.preventDefault();
    const inputText = event.target.value;

    if (inputText.trim().length < 8  ) {
        validPassword = false;
        checkButton();
        passwordError1.innerHTML = "Password is too short. Minimum 8 characters";
         passwordError2.innerHTML = "";

    }

    else if (passwordInput2!= null && passwordInput2.value.length > 7 && inputText != passwordInput2.value) {
          passwordError2.innerHTML = "Passwords arent the same";
          passwordError1.innerHTML="";
          validPassword = false;
          checkButton();
      }
    else {
        checkButton();
        passwordError2.innerHTML="";
        passwordError1.innerHTML = "";
    }
})

passwordInput2.addEventListener('input', (event) => {
    event.preventDefault();
    const inputText = event.target.value;
    if (inputText != passwordInput1.value ) {
        passwordError2.innerHTML = "Passwords arent the same";
        validPassword = false;
        checkButton();
    } else if (inputText == passwordInput1.value &&  passwordInput1.value.length <8){
        validPassword = false;
        passwordError2.innerHTML = "";
        passwordError1.innerHTML = "Password is too short";
        checkButton();
    }
    else  {
        validPassword = true;
        passwordError2.innerHTML = "";
        passwordError1.innerHTML = "";
        checkButton();
    }
})

function checkButton() {
    if (validLogin && validName && validPassword && validEmail) {
        button.disabled = false;
    } else {
        button.disabled = true;
    }
}

checkButton();

