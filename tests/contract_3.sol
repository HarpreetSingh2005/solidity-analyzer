// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TransferSafe {
    mapping(address => uint) public balances;

    function withdraw() public {
        uint amount = balances[msg.sender];

        balances[msg.sender] = 0;

        payable(msg.sender).transfer(amount);
    }
}
