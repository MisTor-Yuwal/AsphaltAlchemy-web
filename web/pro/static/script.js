document.addEventListener('DOMContentLoaded', function() {
    const initiatePopupBtn = document.getElementById('paymentLink');
    const QRPopupCon = document.getElementById('qrPopupMainCont');
    const QrPopupCloseBtn = document.getElementById('CloseQrpopup');
    const overLay = document.getElementById('overlay');

    initiatePopupBtn.addEventListener('click', () => {
        QRPopupCon.style.display = 'block';
        QRPopupCon.classList.remove('backward-out')
        QRPopupCon.classList.add('upward-in');

    });

    function ClosePopup() {
        QRPopupCon.classList.remove('upward-in');
        QRPopupCon.classList.add('backward-out');

        setTimeout(() => {
            QRPopupCon.style.display = 'none';
            QRPopupCon.classList.remove('backward-out');
        }, 500);
    }
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape')
        {   
            ClosePopup();
        }
    }); 
    /*
    overLay.addEventListener('click', function(event){
        if(event.target === overLay)
        {
            ClosePopup();
        }
    });
    */
    QrPopupCloseBtn.addEventListener('click', () => {
        ClosePopup();
    } ) ; 
});

document.addEventListener('DOMContentLoaded', () => {
    const viewBtnForMyOrder = document.querySelectorAll('.myorder-card-viewdetail-btn');
    const myOrderViewPopup = document.getElementById('myOrderPopupSection');
    const myOrderClosePopup = document.getElementById('myOrderClosePopup');


   
    viewBtnForMyOrder.forEach(btn => {
        btn.addEventListener('click', ()=> {
            const orderID = btn.getAttribute('data-order-id');

            fetch(`/${orderID}/details`)
                .then(response => response.json())
                .then(data => {
                    const items = data.items;

                    const template = document.getElementById('myOrderItemTemplate');
                    const cardContainer = document.getElementById('myOrderItemCardContainer');

                    cardContainer.innerHTML= '';

                    items.forEach(item => {
                        const clone = template.cloneNode(true);
                        clone.style.display = 'flex';
                        clone.removeAttribute('id');


                        const imgSEc = clone.querySelector('.myorder-item-card-img-inner-sec');
                        imgSEc.innerHTML = `<img class="myOrderImgSection" src="${baseURLForUserMyOrder}${item.product_image}">`;

                        const proDuctDetail = clone.querySelector('.myorder-item-card-product-details-first');
                        proDuctDetail.innerHTML = `
                        <span class="wdxl-lubrifont-tc-regular myorderfonts">${item.product_name}</span>
                        <span class="wdxl-lubrifont-tc-regular myorderfont">Color : ${item.product_color}, Size : ${item.product_size}</span>
                        `;

                        const productDetailLower = clone.querySelector('.myorder-item-card-product-details-second');
                        productDetailLower.innerHTML = `
                        <span class="wdxl-lubrifont-tc-regular myorderfonts myorderQty">Qty : ${item.product_quantity}</span>
                        `;

                        const myorderItemCardPrice = clone.querySelector('.myorder-item-card-product-extra-details');
                        myorderItemCardPrice.innerHTML = `
                        <span class="wdxl-lubrifont-tc-regular myorderfonts">Rs : ${item.product_price}</span>
                        `;
                        cardContainer.appendChild(clone);
                    });
                    const fuckingSpanCont = document.getElementById('myorder-fucking-total-price');
                    fuckingSpanCont.innerHTML = '';

                    fuckingSpanCont.innerText = `Total : ${data.total_price}`;

                    myOrderClosePopup.addEventListener('click', () => {
                        myOrderViewPopup.classList.remove('upward-in');
                        myOrderViewPopup.classList.add('backward-out');

                        setTimeout(() => {
                            myOrderViewPopup.style.display = 'none';
                            myOrderViewPopup.classList.remove('backward-out');
                        }, 500);
                    });
                });
            myOrderViewPopup.classList.remove('backward-out');
            myOrderViewPopup.classList.add('upward-in');
            myOrderViewPopup.style.display = 'block';
        });
    });
});