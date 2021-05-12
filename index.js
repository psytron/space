
// IMPORT DEPS 
const fs = require('fs');
const hre = require("hardhat");
//const ethers = require("ethers");
const network_name = hre.network.name;



// USAGE: module.signer();
async function signer( index = 0 ){
    return new Promise( async function x( resolve ){
        var signers = await ethers.getSigners();
        var s = 3;
        // console.log('   EOA Signer: ', signer.address );
        // console.log('     EOA  Bal: ',( await signer.getBalance() ).toString() );
        resolve( signers[index] );
    });
}




// USAGE: module.create( 'artifact' );
async function create( artifact_identifier ){
    return new Promise( async function x( resolve ){
        const Fac = await ethers.getContractFactory( artifact_identifier );
        const Contract = await Fac.deploy();
        resolve( Contract );
    });
}


async function contracts(){
    // loop spawn 
    return new Promise( (resolve) => {
        setTimeout(() => {
            resolve('resolved');
        }, 2000);
    });
}

var obj = {}
obj.create = create;
obj.signer = signer;
module.exports = obj;