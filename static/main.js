const loginInput = document.querySelector('#login-input');
const firstNameInput = document.querySelector('#firstname');
const lastNameInput = document.querySelector('#lastname');
const loginError = document.querySelector('#login-error');
const loginGood = document.querySelector('#login-good');
const button = document.querySelector('#register');

const BASE_URL = 'https://infinite-hamlet-29399.herokuapp.com/check';
const errorMessagelogin = 'Username has already exist';
const errorMessageLogin2 = 'Login is too short!';
let validName = false;
let validPassword = false;
let validLogin = false;
const passwordInput1 = document.querySelector('#password-input1');
const passwordInput2 = document.querySelector('#password-input2');
const passwordError1 = document.querySelector('#password-error1');
const firstNameError = document.querySelector('#firstname-error');
const lastNameError = document.querySelector('#lastname-error');
const passwordError2 = document.querySelector('#password-error2');
const request = async (endpoint) => {
    return await fetch(`${BASE_URL}/${endpoint}`)
        .then(response => response.json())
}


const isInputTextMatch = (inputText, username) => {
    const regex = new RegExp(`^${inputText}`, "i");
    return regex.test(username)
}

firstNameInput.addEventListener('input', (evt )=>{
    const regExp = new RegExp("[A-Z]{1}[a-z]");
    if(!regExp.test(firstNameInput.value)){
        validName = false;
        firstNameError.innerText = "Name has to have  first letter big = [A-Z]{1}[a-z]";
        checkButton();
    }
    else{
        firstNameError.innerText = "";
        validName=true;
        checkButton();
    }
});

lastNameInput.addEventListener('input', (evt )=>{
    const regExp = new RegExp("[A-Z]{1}[a-z]");
    if(!regExp.test(lastNameInput.value)){
        lastNameError.innerText = "last name has to have  first letter big = [A-Z]{1}[a-z]";
    }
    else{
        lastNameError.innerText = "";
    }
});



loginInput.addEventListener('input', (event) => {
    event.preventDefault();
    const inputText = event.target.value;

    if (inputText.trim().length < 4) {
        loginGood.innerText = "";
        loginError.innerHTML = errorMessageLogin2;
        validLogin = false;
        checkButton();
    } else {
        loginError.innerHTML = ""
        request(loginInput.value).then(response => {
            if (response[loginInput.value] === "available") {
                validLogin = true;
                loginError.innerText = "";
                loginGood.innerText = "Login is available";
                checkButton();
            } else if (response[loginInput.value] === "taken") {
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

    if (inputText.trim().length < 8) {
        validPassword = false;
        checkButton();
        passwordError1.innerHTML = "Password is too short. Minimum 8 characters";

    } else {
        checkButton();
        passwordError1.innerHTML = "";
    }
})

passwordInput2.addEventListener('input', (event) => {
    event.preventDefault();
    const inputText = event.target.value;
    if (inputText != passwordInput1.value) {
        passwordError2.innerHTML = "Passwords arent the same";
        validPassword = false;
        checkButton();
    } else {
        validPassword = true;
        passwordError2.innerHTML = "";
        checkButton();
    }
})

function checkButton() {
    if (validLogin && validName && validPassword) {
        button.disabled = false;
    } else {
        button.disabled = true;
    }
}

checkButton();

