const loginInput = document.querySelector('#login-input');
const loginError = document.querySelector('#login-error');
const button = document.querySelector('.button');

const BASE_URL = 'https://infinite-hamlet-29399.herokuapp.com/check';
const errorMessagelogin = 'Username has already exist';
const errorMessageLogin2 = 'Login is too short!';
let validData = false;

const passwordInput1 = document.querySelector('#password-input1');
const passwordInput2 = document.querySelector('#password-input2');
const passwordError1 = document.querySelector('#password-error1');
const passwordError2 = document.querySelector('#password-error2');
const request = async (endpoint) => {
    return await fetch(`${BASE_URL}/${endpoint}`)
    .then(response => response.json())
}



const isInputTextMatch = (inputText, username) => {
    const regex = new RegExp(`^${inputText}`, "i");
    return regex.test(username)
}

loginInput.addEventListener('input', (event)=> {
    event.preventDefault();
    const inputText = event.target.value;
        if(inputText.trim().length < 4){
            loginError.innerHTML = errorMessageLogin2
            validData = false;
        }
    else{
        loginError.innerHTML = ""
        request(loginInput.value).then(response => {

            console.log(response)
           //todo obsłużyć
            // usernames.includes(inputText) ?
            // loginError.innerHTML = errorMessage :
            // loginError.innerHTML = '';
        })}
});
passwordInput1.addEventListener('input', (event)=>{
    event.preventDefault();
     const inputText = event.target.value;
     if(inputText.trim().length<8){
        passwordError1.innerHTML = "Password is too short. Minimum 8 characters";
        validData = false;
     }
     else{
         validData = true;
         passwordError1.innerHTML = "";
     }
})

passwordInput2.addEventListener('input', (event)=>{
    event.preventDefault();
     const inputText = event.target.value;
     if(inputText != passwordInput1.value){
        passwordError2.innerHTML = "Passwords arent the same";
        validData = false;
     }
     else{
         validData=true;
         passwordError2.innerHTML = "";
     }
})
