// tests/vulnerable.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Test {
    uint public balance;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function withdraw() public {
        require(balance > 0);
        payable(msg.sender).transfer(balance); // external call
        balance = 0; // state update after call
    }
}
