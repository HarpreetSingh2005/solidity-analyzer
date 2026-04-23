// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeTimelock {
    uint256 public unlockTime;
    address public owner;

    constructor(uint256 _unlockTime) {
        unlockTime = _unlockTime;
        owner = msg.sender;
    }

    function withdraw() public {
        require(msg.sender == owner, "Not owner");
        require(block.timestamp >= unlockTime, "Not unlocked");
        payable(owner).transfer(address(this).balance);
    }
}