// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SendExample {
    mapping(address => uint) public balances;

    function withdraw() public {
        uint amount = balances[msg.sender];

        // ❌ still external call before update
        payable(msg.sender).send(amount);

        balances[msg.sender] = 0;
    }
}
