// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashPoolDrain {
    uint256 public reserve;

    // Vulnerability: sync() sets reserve to balance. Flash loan can donate, then drain elsewhere or skew price.
    function sync() external {
        reserve = address(this).balance;
    }
}