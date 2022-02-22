// signup
async function sign_checkID(id) {
    let response = await fetch('/sign/checkID', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify(id)
    }).then(result=>result.json());
    
    return response;    
}

async function sign_checkNickname(nickname) {    
    let response = await fetch('/sign/checkNickname', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify(nickname)
    }).then(result=>result.json());

    return response;
}

async function sign_signup(id,password,nickname) {
    let response = await fetch('/sign/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify({ 
            'id_give': id,
            'pass_give': password,
            'nickname_give': nickname
        })
    }).then(result=>{
        console.log(result);
        if(result.ok) return result.json();
        else return null;
    });

    return response;
}

//  sign in
async function sign_signin(id,password) {
    let response = await fetch('/sign/signin',{
            method:"POST",
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify({
                'id_give': id,
                'pass_give': password,
            })
        }).then(result=>{
            if(result.ok) return result.json();
            else return null;
        });

    return response;
}

// sign out
function sign_signout() {
    unset_token();
}

// status
function unset_token() {
    fetch('/unset_token');
}

async function get_access_token() {
    let result = await fetch('get_access_token');
    let token = '';

    if(result.ok) token = await result.json();

    return token;
}

async function get_refresh_token() {
    let result = await fetch('get_refresh_token');
    let token = '';

    if(result.ok) token = await result.json();
    console.log(token);
    return token;
}

function refreshing() {
    console.log("리프레싱 시작")
    fetch("/refresh");
}

function get_payload(token) {

    //console.log(token)

    let payload = '';
    if(token){
        let base64Payload = token.split('.')[1]; //value 0 -> header, 1 -> payload, 2 -> VERIFY SIGNATURE
        payload = atob(base64Payload);

        //console.log(payload);
    }
    return payload;
}

function get_payload_exp(token) {

    let exp = get_payload(token).split("exp")[1].slice(2,12);
    //console.log(exp);

    return +exp;
}

async function sign_checkSign() {
    let isSign = false;
    let date = new Date();
    let numberic_date = parseInt(date/1000);
    //console.log('now date:'+numberic_date);

    let access_token = await get_access_token();
    //console.log('access token:'+access_token);
    if(access_token) {
        let access_payload_exp = get_payload_exp(access_token);
        //console.log("access exp:"+access_payload_exp)

        if(access_payload_exp > numberic_date) {
            isSign = true;
        } else {

            let refresh_token = await get_refresh_token();
            let refresh_payload_exp = get_payload_exp(refresh_token);
            console.log("refresh exp:"+refresh_payload_exp)
            if(refresh_payload_exp > numberic_date) {
                refreshing();
                isSign = true;
            }
        }
    }
    return isSign;
}

// sign information
async function sign_getNickname() {
    let nickname = await fetch('/sign/getNickname')
        .then(result=>result.json())
        .then(result=>result['nickname'])

    return nickname
}

async function sign_delete(password) {
    await sign_checkSign();

    //let access_token = await get_access_token();

    let response = await fetch('/sign/delete_user',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8',

            //"Authorization": "Bearer "+ access_token
        },
        body: JSON.stringify({'pass_give': password})
    }).then(result=>result.json());
    
    return response;
}

async function sign_changePassword(currentPassword,newPassword) {
    await sign_checkSign();   
    //let access_token = await get_access_token();
    let response = await fetch('/sign/change_pass',{
            method:"POST",
            headers: {
                'Content-Type': 'application/json;charset=utf-8',
                //"Authorization": "Bearer "+ access_token
            },
            body: JSON.stringify({
                'pass_give': currentPassword,
                'new_pass_give': newPassword                    
            })
        }).then(result=>result.json());

    return response;    
}

//Check Admin
async function sign_checkAdmin() {
    let isAdmin = await fetch('sign/checkAdmin')
        .then(result=>result.json());
    console.log(typeof isAdmin['check'])

    return isAdmin['check']
}