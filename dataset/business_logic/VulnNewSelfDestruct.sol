// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Unprotected selfdestruct can destroy contract and send ETH to anyone.
contract VulnNewSelfDestruct {
    function kill() external {
        selfdestruct(payable(msg.sender)); // Anyone can call this
    }
}