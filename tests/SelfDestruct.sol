// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SelfDestruct {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // Vulnerable: unprotected selfdestruct
    function kill() public {
        selfdestruct(payable(owner));
    }
}
