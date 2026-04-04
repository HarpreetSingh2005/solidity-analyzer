// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract NestedCall {
    mapping(address => uint) public balances;

    function withdraw() public {
        uint amount = balances[msg.sender];

        // ❌ call inside require
        // (bool success, ) = msg.sender.call{value: amount}("");
        require(success);

        balances[msg.sender] = 0;
    }
}
