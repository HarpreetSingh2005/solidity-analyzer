// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe payment splitter distributing ether proportionally.
contract SafePaymentSplitter {
    address[] public payees;
    mapping(address => uint256) public shares;
    uint256 public totalShares;
    uint256 public totalReleased;
    mapping(address => uint256) public released;

    constructor(address[] memory _payees, uint256[] memory _shares) {
        require(_payees.length == _shares.length, "Lengths mismatch");
        require(_payees.length > 0, "No payees");

        for (uint256 i = 0; i < _payees.length; i++) {
            require(_payees[i] != address(0), "Zero address");
            require(_shares[i] > 0, "Zero shares");

            payees.push(_payees[i]);
            shares[_payees[i]] = _shares[i];
            totalShares += _shares[i];
        }
    }

    receive() external payable {}

    function release(address payee) public {
        require(shares[payee] > 0, "No shares");

        uint256 totalReceived = address(this).balance + totalReleased;
        uint256 payment = (totalReceived * shares[payee]) / totalShares - released[payee];
        
        require(payment > 0, "No payment due");

        released[payee] += payment;
        totalReleased += payment;

        (bool success, ) = payee.call{value: payment}("");
        require(success, "Transfer failed");
    }
}