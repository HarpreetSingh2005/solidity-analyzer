// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract RewardDoubleClaim {
    mapping(address => bool) public claimed;
    function claimReward() external {
        require(!claimed[msg.sender], "Already claimed");
        claimed[msg.sender] = true;
        payable(msg.sender).transfer(1 ether);
    }
}