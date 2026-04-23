// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract ShareInflation {
    uint256 public totalAssets;
    uint256 public totalShares;
    function deposit() external payable {
        if (totalShares == 0) {
            totalShares = msg.value; // BUG: first depositor attack
        }
    }
}