// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TxOrigin {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // Vulnerable: uses tx.origin for authentication
    function withdrawAll() public {
        require(tx.origin == owner, "Not owner");
        payable(msg.sender).transfer(address(this).balance);
    }
}
