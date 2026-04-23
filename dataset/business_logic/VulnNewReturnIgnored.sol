// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Return value of low-level call is ignored.
contract VulnNewReturnIgnored {
    function sendTokens(address to, uint256 amount) external {
        // Silent failure if the token transfer fails
        to.call(abi.encodeWithSignature("transfer(address,uint256)", to, amount));
    }
}