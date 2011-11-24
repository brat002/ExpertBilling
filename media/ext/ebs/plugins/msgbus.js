// vim: sw=4:ts=4:nu:nospell:fdc=4
/**
 * Message Bus Plugin
 *
 * @author    Ing. Jozef Sakáloš
 * @copyright (c) 2009, by Ing. Jozef Sakáloš
 * @date      19. September 2009
 * @version   $Id: Ext.ux.MsgBus.js 29 2009-09-23 09:51:55Z jozo $
 *
 * @license Ext.ux.MsgBus.js is licensed under the terms of the Open Source
 * LGPL 3.0 license. Commercial use is permitted to the extent that the 
 * code/component(s) do NOT become part of another Open Source or Commercially
 * licensed development library or toolkit without explicit permission.
 * 
 * License details: http://www.gnu.org/licenses/lgpl.html
 */
 
/*global Ext,window */
 
/**
 * @class Ext.ux.MsgBus
 *
 * Creates new Ext.ux.MsgBus object
 * @constructor
 * @param {Object} config The config object
 */
Ext.ux.MsgBus = function(config) {
    Ext.apply(this, config, {
    });
}; // eo constructor
 
Ext.override(Ext.ux.MsgBus, {
    /**
     * @cfg {String} busName Name of the global Observable instance
     */
     busName:'Ext.ux.Bus'
    /**
     * @private
     */
    ,bus:false
    /**
     * Initializes the plugin and component
     * @private
     */
    ,init:function(cmp) {
        this.cmp = cmp;
        cmp.bus = this.getBus();
        cmp.bus.addEvents('message');
        cmp.subs = {};
        this.applyConfig();
    } // eo function init
    // {{{
    /**
     * Returns or creates the global Observable instance
     * @private
     */
    ,getBus:function() {
        var bus = window;
        var a = this.busName.split('.');
        var last = a.pop();
        Ext.each(a, function(n) {
            if(!Ext.isObject(bus[n])) {
                bus = false;
                return false;
            }
            else {
                bus = bus[n];
            }
        }, this);
        if(false === bus) {
            Ext.ns(this.busName);
            return this.getBus();
        }
        if(!(bus[last] instanceof Ext.util.Observable)) {
            bus[last] = new Ext.util.Observable();
        }
        return bus[last];
    } // eo function getBus
    // }}}
    // {{{
    /**
     * Creates RegExp for message filtering.
     * Override it if you need another logic.
     * @param {String} subject The message subject
     * @return {RegExp} RegExp used for message filtering
     */
    ,getFilterRe:function(subject) {
        var a = subject.split('.');
        var last = a.length - 1;
        a[last] = '**' === a[last] ? '.*' : a[last];
        var re = /^\w+$/;
        Ext.each(a, function(token, i) {
            if(!re.test(token) && '*' !== token && '.*' !== token) {
                throw 'Invalid subject: ' + subject;
            }
            if('*' === token) {
                a[i] = '\\w+';
            }
        });
        return new RegExp('^' + a.join('\\.') + '$');
    } // eo function getFilter
    // }}}
    // {{{
    /**
     * Applies new methods to the component
     * @private
     */
    ,applyConfig:function() {
        Ext.applyIf(this.cmp, {
            /**
             * Subscribes to messages (parent component method)
             * @param {String} subject Dotted notation subject with wildcards.
             * See http://www.openajax.org/member/wiki/OpenAjax_Hub_2.0_Specification_Topic_Names
             * @param {Object} config Same as addListener config object
             * @return {Boolean} success true on success, false on failure (subscription exists)
             */
             subscribe:function(subject, config) {
                 var sub = this.subs[subject];
                if(sub) {
                    return false;
                }
                config = config || {};
                config.filter = this.getFilterRe(subject);
                this.subs[subject] = {config:config, fn:this.filterMessage.createDelegate(this, [config], true)};
                this.bus.on('message', this.subs[subject].fn, config.scope || this, config);
                return true;
            }
 
            /**
             * Unsubscribes from messages (parent component method)
             * @param {String} subject Dotted notation subject with wildcards.
             * @return {Boolean} success true on success, false on failure (nonexistent subscription)
             */
            ,unsubscribe:function(subject) {
                var sub = this.subs[subject];
                if(!sub) {
                    return false;
                }
                this.bus.un('message', sub.fn, sub.scope || this, sub.config);
                delete this.subs[subject];
                sub = null;
                return true;
            } // eo function unsubscribe
 
            /**
             * Publishes the message (parent component method)
             * @param {String} subject Message subject
             * @param {Mixed} message Message body, most likely an object
             */
            ,publish:function(subject, message) {
                this.getFilterRe(subject);
                this.bus.fireEvent('message', subject, message);
            } // eo function publish
 
            /**
             * Returns current subscriptions
             * @return {Object} subscriptions
             */
            ,getSubscriptions:function() {
                return this.subs;
            } // eo function
 
            /**
             * @private
             */
            ,getFilterRe:this.getFilterRe
 
            /**
             * Filters incoming messages
             * @private
             */
            ,filterMessage:function(subject, message, config) {
                if(config.filter.test(subject)) {
                    (config.fn || this.onMessage).call(config.scope || this, subject, message);
                }
            } // eo function filterMessage
 
            /**
             * Default message processing function
             * @param {String} subject The message subject
             * @param {Mixed} message The message body
             */
            ,onMessage:Ext.emptyFn
        });
    } // eo function applyConfig
    // }}}
 
}); // eo override
 
// register ptype
Ext.preg('msgbus', Ext.ux.MsgBus); 
.6