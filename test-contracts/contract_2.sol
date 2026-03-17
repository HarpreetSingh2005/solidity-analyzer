// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ReentrancySafe {
    mapping(address => uint) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint amount = balances[msg.sender];

        // ✅ State update FIRST
        balances[msg.sender] = 0;

        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);
    }
}
