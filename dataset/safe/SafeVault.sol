// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe timelock vault allowing time-based withdrawals.
contract SafeVault {
    mapping(address => uint256) public balances;
    mapping(address => uint256) public lockTime;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
        lockTime[msg.sender] = block.timestamp + 1 weeks;
    }

    function withdraw() external {
        require(balances[msg.sender] > 0, "No funds");
        require(block.timestamp > lockTime[msg.sender], "Lock time not expired");

        uint256 amount = balances[msg.sender];
        balances[msg.sender] = 0;

        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
}