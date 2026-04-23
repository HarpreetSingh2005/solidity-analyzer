// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Reentrancy in flash loan callback.
contract VulnNewFlashCallback {
    uint256 public balance;
    function flashLoan(uint256 amount, address receiver) external {
        uint256 oldBalance = balance;
        // Vulnerable: Callback before state update
        (bool s, ) = receiver.call(abi.encodeWithSignature("execute()"));
        require(s);
        require(balance >= oldBalance, "Not repaid");
    }
}