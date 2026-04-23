// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashDividend {
    mapping(address => uint256) public shares;
    uint256 public totalDividendPool;

    // Vulnerability: Flash loan can be used to buy shares, claim dividend, and sell shares in 1 tx
    function claimDividend() external {
        uint256 dividend = (shares[msg.sender] * totalDividendPool) / 10000;
        shares[msg.sender] = 0; // Resets shares, but can be rebought
        payable(msg.sender).transfer(dividend);
    }
}