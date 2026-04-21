// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ShadowedVariable {
    uint256 public balance;     // State variable

    // This function has a parameter with the same name as the state variable
    function setBalance(uint256 balance) public {   
        // BUG: This only updates the local parameter, NOT the state variable
        balance = balance + 100;   

        // Correct way would be:
        // this.balance = balance + 100; or use a different name like _balance
    }
}