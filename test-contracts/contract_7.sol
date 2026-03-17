// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MultiUpdate {
    mapping(address => uint) public balances;

    function withdraw() public {
        balances[msg.sender] -= 10;

        (bool success, ) = msg.sender.call{value: 10}("");
        require(success);

        balances[msg.sender] = 0;
    }
}
