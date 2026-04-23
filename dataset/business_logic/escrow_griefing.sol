// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract EscrowGriefing {
    uint256 public expectedAmount;
    address public buyer;
    address public seller;
    constructor(address _seller, uint256 _amount) payable {
        buyer = msg.sender;
        seller = _seller;
        expectedAmount = _amount;
    }
    function confirmPayment() external payable {
        require(address(this).balance == expectedAmount, "Incorrect amount"); // BUG: dust griefing
        payable(seller).transfer(address(this).balance);
    }
    receive() external payable {}
}