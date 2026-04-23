// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Weak randomness using block.timestamp.
contract VulnNewLotteryManip {
    function play() external payable {
        require(msg.value == 1 ether, "Send 1 ETH");
        if (uint256(keccak256(abi.encodePacked(block.timestamp, msg.sender))) % 2 == 0) {
            payable(msg.sender).transfer(2 ether);
        }
    }
}