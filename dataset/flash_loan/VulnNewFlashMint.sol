// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: LP tokens minted based on manipulatable spot ratio.
contract VulnNewFlashMint {
    uint256 public totalLP;
    function addLiquidity() external payable {
        // Total LP minted depends on address(this).balance which can be flash-loaned
        uint256 lp = msg.value * totalLP / address(this).balance; 
        totalLP += lp;
    }
}