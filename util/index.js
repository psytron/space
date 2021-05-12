
// IMPORT DEPS 
const fs = require('fs');
const hre = require("hardhat");
const ethers = require("ethers");
const network_name = hre.network.name;

// USAGE 
// call_sig(  'methodName' , ['type','type'] , ['val','val'] );


function call_sig( method_name , types_arr , vals_arr  ){
    var types_array = types_arr;
    var types_array_string = types_array.join(',');
    var funcSig = method_name + '('+types_array_string+')';
    let funcBytes = ethers.utils.toUtf8Bytes( funcSig );
    var funcKeccak = ethers.utils.keccak256( funcBytes );
    var funcSegment = funcKeccak.slice(0,10);
    let bbPack = ethers.utils.solidityPack(
        [ 'bytes4', ...types_arr ], 
        [ funcSegment, ...vals_arr ] );
    return bbPack;
}

function push( name , dat  ){
    var method_name = 'add0';
    //var method_name = 'ping2';
    var types_array = ['uint256','uint256'];
    var types_array_string = types_array.join(',');
    var funcSig = method_name + '('+types_array_string+')';
    console.log( 'funcSig1: ', funcSig );
    let funcBytes = ethers.utils.toUtf8Bytes( funcSig );
    var funcKeccak = ethers.utils.keccak256( funcBytes );
    var funcSegment = funcKeccak.slice(0,10);
    let bbPack = ethers.utils.solidityPack(
        [ 'bytes4','uint256', 'uint256'], 
        [  funcSegment,  5  ,   5  ] );
}


var obj = {}
obj.push = push;
obj.call_sig = call_sig;
module.exports = obj;